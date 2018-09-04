""" Various utility functions that dont have an obvious home """

import math
import os
import os.path
import time

def reset_stats(file_path):
    """ Do some file cleanup"""
    if os.path.isfile(file_path):
        os.remove(file_path)

def map_to_cartesian(lat, lon):
    """gross mapping to cartesian plane"""
    # Make everything a float so you dont have to worry about it
    if not isinstance(lat, float):
        lat = float(lat)
    if not isinstance(lon, float):
        lon = float(lon)

    # Do mercator stuff
    map_width = 400
    map_height = 200

    x_coord = (lon + 180.0) * (map_width/360.0)
    lat_rad = lat * (math.pi / 180.0)
    merc_n = math.log(math.tan((math.pi/4) + (lat_rad/2)))
    y_coord = (map_height/2) - (map_width * merc_n / (2 * math.pi))

    y_coord = y_coord * -1

    return (x_coord, y_coord)


def convert_to_local(curr_time):
    """ Take a time stamp input and convert to seconds since midnight """

    midnight = list(time.localtime(curr_time))
    # Set hour, minute, sec to 0
    midnight[3] = 0
    midnight[4] = 0
    midnight[5] = 0

    midnight_sec = time.mktime(time.struct_time(midnight))

    return curr_time - midnight_sec
