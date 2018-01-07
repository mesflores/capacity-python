""" Reads gtfs files and builds a network with them """

import json
import logging
import os.path

def read_gtfs_files(data_dir):
    """ Read all the files and load them into python dict raw"""
    gtfs_info = {}

    # GTFS sfiles standards
    gtfs_req_files = [
        "agency",
        "stops",
        "routes",
        "trips",
        "stop_times",
        "calendar",
        # There are others but not required. Someday.
    ]

    for gtfs_file in gtfs_req_files:
        # build the actual file name
        file_name = gtfs_file + ".txt"
        file_name = os.path.join(data_dir, file_name)
        with open(file_name) as gtfs_file_obj:
            # Just dump the whole thing into mem.
            # these might be kind of big in some cases...
            gtfs_info[gtfs_file] = gtfs_file_obj.read()

    return gtfs_info

def parse_routes(raw_gtfs):
    """ Dump the route stuff into a dictionary"""
    route_info = {}

    # Ok let's crack open each line
    for index, line in enumerate(raw_gtfs["routes"].split("\n")):
        # it's the header
        if index == 0:
            label_list = line.split(',')
            continue
        # Otherwise it's a data row
        # Loop over the columns in that row
        for c_index, data in enumerate(line.split(',')):
            # if its the first column it's just the route id
            if c_index == 0:
                route_id = data
                # Quick sanity check
                if route_id in route_info:
                    raise RuntimeError("Got a route ID we already had!")
                # Make a dict
                route_info[route_id] = {}
                continue
            # Stape it into our new dict
            route_info[route_id][label_list[c_index]] = data

    return route_info

def load_gtfs_data(data_dir):
    """Does all the heavy lifting returns everything in a nice dict"""
    raw_data = read_gtfs_files(data_dir)

    print(raw_data["agency"])

    # More or less, it will look something like this:
    # Trips-> turn into trains + routes

    route_info = parse_routes(raw_data)

    print(json.dumps(route_info, indent=4))

    return raw_data
