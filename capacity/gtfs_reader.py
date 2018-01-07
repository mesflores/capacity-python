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
            gtfs_info[gtfs_file] = gtfs_file_obj.read().strip()

    return gtfs_info

def parse_gtfs_file(raw_file, key_column):
    """Parse a GTFS file, with key column being the unique key"""
    parse_info = {}
    # Spin through the lines
    for index, line in enumerate(raw_file.split("\n")):
        # If its the first one, learn the column positions
        if index == 0:
            columns = line.split(",")
            key_index = columns.index(key_column)

        # Otherwise it's a data row
        # First, get the value from the key column...
        split_row = line.split(',')
        key_val = split_row[key_index]

        # Make a new dict for this row
        parse_info[key_val] = {}

        # Ok now spin over the remaining values
        for c_index, data in enumerate(split_row):
            # Just skip over the key column
            if c_index == key_index:
                continue
            # Get the name from the header
            c_name = columns[c_index]
            # Stick it in the appropriate dict with the column name
            parse_info[key_val][c_name] = data

    return parse_info

def load_gtfs_data(data_dir):
    """Does all the heavy lifting returns everything in a nice dict"""
    raw_data = read_gtfs_files(data_dir)

    print(raw_data["agency"])

    # More or less, it will look something like this:
    # Trips-> turn into trains + routes

    route_info = parse_gtfs_file(raw_data["routes"], "route_id")
    print(json.dumps(route_info, indent=4))

    return raw_data
