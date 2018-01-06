"""Capacity -- A transit simulator I guess """

import argparse

import simpy

import capacity.network as network
import capacity.train as train


def simple_system():
    """ Create a simple system for debugging """
    # Make the simpy env
    env = simpy.Environment()

    # Create the the network object
    system = network.TransitNetwork(env)
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

def load_gtfs(gtfs_dir):
    """ Create a network from GTFS data """
    # Make the simpy
    env = simpy.Environment() 

    # Create the network
    system = network.TransitNetwork(env)
    
    # Call the GTFS func
    system.read_gtfs(gtfs_dir)

    # XXX Do stuff?
    raise NotImplementedError

def main():
    """ main func"""
    parser = argparse.ArgumentParser(description="A transit simulator, I guess")

    parser.add_argument("--simple", action="store_true",
                        help="Run the simple example")
    parser.add_argument("--load_gtfs", action="store", type=str,
                        help="Run a system built from gtfs files")

    args = parser.parse_args()

    # Run the simple thing
    if args.simple:
        simple_system()
    if args.load_gtfs:
        load_gtfs(args.load_gtfs)

