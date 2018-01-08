""" Reads gtfs files and builds a network with them """

import datetime
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

def filter_stops(stop_info):
    """ Filter for only type 0 stops, ie load/unload"""

    new_stop_info = {}
    for stop in stop_info:
        if stop_info[stop]["location_type"] == "0":
            new_stop_info[stop] = stop_info[stop]

    return new_stop_info

def load_stop_times(stop_times_raw):
    """Load the stop times into a big dict"""
    # NOTE: This is maybe possible with the above parsing function, but
    # would be a little complicated since there is no key in the same way, and
    # I just want the sequences to go in a list
    stop_times = {}
    # Spin through the lines
    for index, line in enumerate(stop_times_raw.split("\n")):
        # If its the first one, learn the column positions
        if index == 0:
            columns = line.split(",")
            key_index = columns.index("trip_id")
            continue
        # Get the trip_id
        data_row = line.split(",")
        trip_id = data_row[key_index]

        # did we have this?
        if trip_id not in stop_times:
            stop_times[trip_id] = []

        # Make a dict for this one
        trip_stop = {columns[x]: data for x, data in enumerate(data_row)}

        # Type cleaning
        trip_stop["stop_sequence"] = int(trip_stop["stop_sequence"])

        # Add it to the list
        stop_times[trip_id].append(trip_stop)

    # Sort them all by sequence number. Probably we could do that at insert,
    # but fuck it
    for trip in stop_times:
        stop_times[trip].sort(key=lambda x: x["stop_sequence"])

    return stop_times

def build_stop_adj_matrix(stop_times):
    """Given a set of stop times, build an adjacencey matrix """

    stop_adj = {}

    for trip in stop_times:
        curr_trip = stop_times[trip]
        # Loop through the seq of stops
        for index, stop in enumerate(curr_trip):
            # If its the first one, just move on
            if index == 0:
                continue

            # Where did I come from?
            prev = curr_trip[index - 1]
            prev_id = prev["stop_id"]

            # Put it in adj matrix if needed
            if prev_id not in stop_adj:
                stop_adj[prev_id] = {}

            # What's the time between the two?
            # TODO Getting hacky with time, assuming no DST silly
            depart_components = prev["departure_time"].split(":")
            depart_components[0] = str(int(depart_components[0]) % 24)
            depart_time = datetime.datetime.strptime(":".join(depart_components),
                                                     "%H:%M:%S")
            arrive_components = stop["arrival_time"].split(":")
            arrive_components[0] = str(int(arrive_components[0]) % 24)
            arrive_string = ":".join(arrive_components)
            arrive_time = datetime.datetime.strptime(arrive_string,
                                                     "%H:%M:%S")

            # TODO: That mod to deal with day wrap around is real sketchy
            weight = (arrive_time - depart_time).total_seconds() % 86400

            # Save the minimum wieght in the matrix, ie the min time between stations
            if stop["stop_id"] in stop_adj[prev_id]:
                curr = stop_adj[prev_id][stop["stop_id"]]
                weight = min(curr, weight)

            # Stick it in the matrix
            stop_adj[prev_id][stop["stop_id"]] = weight

    return stop_adj

def load_gtfs_data(data_dir):
    """Does all the heavy lifting returns everything in a nice dict"""
    raw_data = read_gtfs_files(data_dir)

    print(raw_data["agency"])

    # More or less, it will look something like this:
    # Trips-> turn into trains + routes

    route_info = parse_gtfs_file(raw_data["routes"], "route_id")

    # Load the set of stops
    stop_info = parse_gtfs_file(raw_data["stops"], "stop_id")
    # Filter for actual load/unload, remove entrances
    stop_info = filter_stops(stop_info)

    trip_info = parse_gtfs_file(raw_data["trips"], "trip_id")

    stop_times = load_stop_times(raw_data["stop_times"])

    #print(json.dumps(stop_times, indent=4))

    adj_matrix = build_stop_adj_matrix(stop_times)

    # Stick it all in a dict for now
    gtfs_data = {}
    gtfs_data["routes"] = route_info
    gtfs_data["stops"] = stop_info
    gtfs_data["trip_info"] = trip_info
    gtfs_data["stop_times"] = stop_times
    gtfs_data["adj_matrix"] = adj_matrix

    return gtfs_data
