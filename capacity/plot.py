""" Plot -- make some handy plots """
import csv

from collections import defaultdict

import numpy as np

from matplotlib import pyplot as plt

from capacity.conf import TRAVELER_STATS_FILE

def plot_cdf(data_list):
    """Plot the CDF of the sets in data_lsit"""

    for label, data in data_list:

        sorted_x = np.sort(data)
        yvals = np.arange(len(sorted_x))/float(len(sorted_x))
        plt.plot(sorted_x, yvals, label=label)

    plt.legend(frameon=False)

    plt.show()


def plot_traveler_time():
    """Plot some stuff about traveler time"""

    mode_dict = defaultdict(list)

    with open(TRAVELER_STATS_FILE) as stat_file:
        reader = csv.reader(stat_file)
        for start, dest, wait, ride, transfer in reader:
            mode_dict["wait"].append(float(wait))
            mode_dict["ride"].append(float(ride))
            mode_dict["transfer"].append((transfer))

    plot_list = [
        ("Wait", mode_dict["wait"]),
        ("Ride", mode_dict["ride"]),
        ]

    plot_cdf(plot_list)
