""" The master network object """

import networkx as nx

import capacity.station as station
import capacity.train as train

class TransitNetwork(object):
    """ The master container class for the transit network object """
    def __init__(self, env):
        """Creat the graph object initstations and add them """

        # The process env for simpy
        self.env = env

        # The stations in the network
        self.station_dict = {}

        # Trains in the network
        self.trains = []

        # The graph that describes connections between stations
        # The stations are stored as integers
        self._connect_graph = nx.DiGraph()

    def get_distance(self, src, dst):
        """ Look up the weight between two stations """
        return self._connect_graph.get_edge_data(src, dst)["weight"]

    def add_station(self, station_id, name):
        """ Add a new station """
        # Create the object
        new_station = station.Station(station_id, name, self)
        # stick it in the dict
        self.station_dict[station_id] = new_station
        # Add it to the graph
        self._connect_graph.add_node(station_id)

    def connect_station_pair(self, source_id, dest_id, weight):
        """ Given two stations, connect them in the graph"""
        self._connect_graph.add_edge(source_id, dest_id, weight=weight)

    def add_train(self, home_station_id, route):
        """ Create a new train """
        new_train = train.Train(home_station_id, self, route)

        # Put the train in the list
        self.trains.append(new_train)
