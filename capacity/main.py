"""Capacity -- A transit simulator I guess """

import argparse
import logging

import simpy

from matplotlib import pyplot as plt

import capacity.network as network
import capacity.train as train


def simple_system():
    """ Create a simple system for debugging """
    # Make the simpy env
    env = simpy.Environment()

    # Create the the network object
    system = network.TransitNetwork(env, "test.out")
    # Add two stations
    system.add_station(1, "A")
    system.add_station(2, "B")
    system.add_station(3, "C")

    # Connect them
    system.connect_station_pair(1, 2, 5)
    system.connect_station_pair(2, 1, 5)
    system.connect_station_pair(2, 3, 3)
    system.connect_station_pair(3, 2, 3)

    #Make a route
    route = train.Route(1, 3, [1, 2, 3])

    # Make a train
    system.add_train(1, route) #Starts at station 1

    env.run(until=20)

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
    system.add_train("80122", route, train.KS_P3010)

    # Run for a little while
    #env.run(until=86400)
    env.run()

    #system.draw_network()
    #plt.show()

def main():
    """ main func"""
    parser = argparse.ArgumentParser(description="A transit simulator, I guess")

    parser.add_argument("--simple", action="store_true",
                        help="Run the simple example")
    parser.add_argument("--load_gtfs", action="store", type=str,
                        help="Run a system built from gtfs files")
    parser.add_argument("--output_file", action="store", type=str,
                        default="capacity.log",
                        help="Location of output file")

    args = parser.parse_args()

    # Config logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.WARN)

    logging.info("Starting...")

    # Run the simple thing
    if args.simple:
        simple_system()
    if args.load_gtfs:
        load_gtfs(args.load_gtfs, args.output_file)
