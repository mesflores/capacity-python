""" Various utility functions that dont have an obvious home """

import math

def map_to_cartesian(lat, lon):
    """gross mapping to cartesian plane"""
    # Make everything a float so you dont have to worry about it
    if not isinstance(lat, float):
        lat = float(lat)
    if not isinstance(lon, float):
        lon = float(lon)

    # Do mercator stuff
    map_width = 200
    map_height = 100

    x_coord = (lon + 180.0) * (map_width/360.0)
    lat_rad = lat * (math.pi / 180.0)
    merc_n = math.log(math.tan((math.pi/4) + (lat_rad/2)))
    y_coord = (map_height/2) - (map_width * merc_n / (2 * math.pi))

    y_coord = y_coord * -1

    return (x_coord, y_coord)
