"""Capacity -- A transit simulator I guess """

import argparse
import os
import os.path
import logging
import sys

import simpy

from matplotlib import pyplot as plt

import capacity.network as network
import capacity.train as train

from capacity.conf import TRAVELER_STATS_FILE

def reset_stats():
    """ Do some file cleanup"""
    # TODO: Replace this with a more robust system that stores "runs"
    if os.path.isfile(TRAVELER_STATS_FILE):
        os.remove(TRAVELER_STATS_FILE)

def simple_system(output_file):
    """ Create a simple system for debugging """
    # Make the simpy env
    env = simpy.Environment()

    # Create the the network object
    system = network.TransitNetwork(env, output_file)
    # Add two stations
    system.add_station(1, "A")
    system.add_station(2, "B")
    system.add_station(3, "C")
    system.add_station(4, "D")

    # Connect them
    system.connect_station_pair(1, 2, 5)
    system.connect_station_pair(2, 1, 5)
    system.connect_station_pair(2, 3, 3)
    system.connect_station_pair(3, 2, 3)
    system.connect_station_pair(3, 4, 4)
    system.connect_station_pair(4, 3, 4)

    #Make a route
    route = train.Route(1, 4, [1, 2, 3, 4])
    route_2 = train.Route(4, 1, [4, 3, 2, 1])

    # Make a train
    system.add_train(1, route) #Starts at station 1
    # Make 2 trains!
    system.add_train(4, route_2) #Starts at station 4

    return (env, system)

def load_gtfs(gtfs_dir, output_file):
    """ Create a network from GTFS data """
    # Make the simpy
    env = simpy.Environment()

    # Create the network
    system = network.TransitNetwork(env, output_file)

    # Call the GTFS func
    system.read_gtfs(gtfs_dir)

    # Let's make a route -- Full Expo run
    stop_list = ["80122", "80121", "80123", "80124", "80125", "80126", "80127",
                 "80128", "80129", "80130", "80131", "80132", "80133", "80134",
                 "80135", "80136", "80137", "80138",
                 "80139"]
    route = train.Route("80122", "80139", stop_list)

    # Add that route to a KS P3010
    system.add_train("80122", route, train_type=train.KS_P3010)


    route2 = train.Route("80139", "80122", stop_list[::-1])
    system.add_train("80139", route2, train_type=train.KS_P3010)

    return (env, system)

def run_system(env, system, until=100):
    """Actually run the whole thing """


    # Run for a little while
    env.run(until=until)

    #system.draw_network()
    #plt.show()

def main():
    """ main func"""
    parser = argparse.ArgumentParser(description="A transit simulator, I guess")

    # Run the simple test, or use GTFS data?
    parser.add_argument("--simple", action="store_true",
                        help="Run the simple example")
    parser.add_argument("--load_gtfs", action="store", type=str,
                        help="Run a system built from gtfs files")
    # Some parameters for the run
    parser.add_argument("--until", action="store", type=int,
                        default="100",
                        help="How long (min) to run the simulation for")
    # Log level
    parser.add_argument("--log_level", action="store", type=str,
                        default="WARN",
                        help="Log level")
    # Log file location
    parser.add_argument("--output_file", action="store", type=str,
                        default="capacity.log",
                        help="Location of output file")

    args = parser.parse_args()

    # Config logging
    numeric_level = getattr(logging, args.log_level.upper(), None)
    logging.basicConfig(format='%(asctime)s %(message)s', level=numeric_level)

    # Reset stats files
    reset_stats()
    
    logging.info("Starting...")

    # Run the simple thing
    if args.simple:
        env, system = simple_system(args.output_file)
    elif args.load_gtfs:
        env, system = load_gtfs(args.load_gtfs, args.output_file)
    else:
        print("Run type required!")
        sys.exit(-1)

    # Now actually run it
    run_system(env, system, until=args.until)
