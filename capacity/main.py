"""Capacity -- A transit simulator I guess """

import simpy

import capacity.network as network
import capacity.train as train

def main():
    """ main func"""
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
