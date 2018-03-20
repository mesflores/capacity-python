""" The master network object """

import errno
import logging
import os

import networkx as nx
import numpy as np

import capacity.gtfs_reader as gtfs_reader
import capacity.station as station
import capacity.stats as stats
import capacity.train as train
import capacity.utils as utils

class TransitNetwork(object):
    """ The master container class for the transit network object """
    def __init__(self, env, output_file, config_dict):
        """Creat the graph object initstations and add them """

        # The process env for simpy
        self.env = env

        # Save your configs so you can pass around
        self.config = config_dict
        # Make the rundir
        try:
            os.makedirs(config_dict["run_dir"])
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise

        # Reset all the output files if needed
        for file_name in self.config["files"]:
            utils.reset_stats(self.config["files"][file_name])

        # Instantuate the models needed
        ## Train delay
        self.train_delay = config_dict["train_delay"]()

        ########

        self.info = ""

        # The stations in the network
        self.station_dict = {}
        self.popularity_dict = {}

        # Trains in the network
        self.trains = []

        # Create and init a stats object
        self.stats = stats.NetworkStats()
        self.stats.init_output(output_file)
        # Fire off the stats loop
        self.stats_action = self.env.process(self.stats.periodic_output(env))

        # The graph that describes connections between stations
        # The stations are stored as integers
        self._connect_graph = nx.DiGraph()

    def read_gtfs(self, gtfs_file_dir):
        """ Create a network with GTFS Data """
        # TODO: Set outputs from this...
        data = gtfs_reader.load_gtfs_data(gtfs_file_dir)

        logging.info("Creating stations...")
        # load all the stops
        for stop in data["stops"]:
            curr_stop = data["stops"][stop]
            self.add_station(stop, curr_stop["stop_name"])
            # Set position with shitty mapping
            xy_pos = utils.map_to_cartesian(curr_stop["stop_lat"],
                                            curr_stop["stop_lon"])
            self.station_dict[stop].set_pos(xy_pos)

        logging.info("Connecting stations...")
        # Spin through the adj_matrix and add all the links
        for src in data["adj_matrix"]:
            for dst in data["adj_matrix"][src]:
                weight = data["adj_matrix"][src][dst]
                self.connect_station_pair(src, dst, weight)

    def draw_network(self):
        """ Draw the network for LOOKING"""
        # Make a dir of the positoons

        logging.info("Drawing network...")

        pos_dir = {}
        name_dir = {}
        positions = True
        for stop in self.station_dict:
            curr_stop = self.station_dict[stop]
            if curr_stop.pos is None:
                positions = False
            pos_dir[stop] = curr_stop.pos
            name_dir[stop] = curr_stop.name

        if positions:
            nx.draw(self._connect_graph, pos=pos_dir, with_labels=True,
                    labels=name_dir,
                    font_size=8,
                    node_size=100,
                   )
        else:
            nx.draw(self._connect_graph, with_labels=True,
                    labels=name_dir,
                    font_size=8,
                    node_size=100,
                   )

    def get_name(self, station_id):
        """ Return the string name of a station"""
        return self.station_dict[station_id].name

    def get_distance(self, src, dst):
        """ Look up the weight between two stations """

        # TODO: Find a better way to handle travel time
        delay = self.train_delay.generate_delay(src, dst)
        return self._connect_graph.get_edge_data(src, dst)["weight"] + delay

    def add_station(self, station_id, name):
        """ Add a new station """
        # Adjsut the name
        if name.endswith("Station"):
            # Chop off the "station"
            name = name[:-8]

        # Create the object
        new_station = station.Station(station_id, name, self)
        # stick it in the dict
        self.station_dict[station_id] = new_station
        # Add it to the graph
        self._connect_graph.add_node(station_id)
        # Add it to the stats
        self.stats.add_station(station_id)

    def connect_station_pair(self, source_id, dest_id, weight):
        """ Given two stations, connect them in the graph"""
        self._connect_graph.add_edge(source_id, dest_id, weight=weight)

    def add_train(self, home_station_id, route, run=None, train_type=None):
        """ Create a new train """
        # If no run name defined, just call it the home station
        if run is None:
            run = home_station_id

        if train_type is None:
            new_train = train.Train(home_station_id, self, route, run)
        else:
            new_train = train_type(home_station_id, self, route, run, 3)

        # Put the train in the list
        self.trains.append(new_train)

    def determine_route(self, start, destination):
        """ Determine the shortest path from start to destination, return a list of all the hops"""
        path = nx.shortest_path(G=self._connect_graph, source=start,
                                target=destination, weight="weight")

        return path
