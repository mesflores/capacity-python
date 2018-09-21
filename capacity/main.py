"""Capacity -- A transit simulator I guess """

import argparse
import datetime
import logging
import sys

import simpy

from matplotlib import pyplot as plt

import capacity.config_reader as config_reader
import capacity.gtfs_reader as gtfs_reader
import capacity.network as network
import capacity.train as train

def load_gtfs(config_dict):
    """ Create a network from GTFS data """
    # Let's do some quick start time math
    earliest_date = gtfs_reader.min_date(config_dict["gtfs_dir"])
    start_date = datetime.datetime.strptime(earliest_date, "%Y%m%d")
    start_sec = start_date.timestamp()

    # Make the simpy
    env = simpy.Environment(start_sec)

    # Create the network
    system = network.TransitNetwork(env, config_dict)

    # Call the GTFS func
    system.read_gtfs(config_dict["gtfs_dir"])

    return (env, system, start_sec)

def run_system(env, system, until=100):
    """Actually run the whole thing """

    # Run for a little while
    env.run(until=until)

    #system.draw_network()
    #plt.show()

def main():
    """ main func"""
    parser = argparse.ArgumentParser(description="A transit simulator, I guess")

    # Some parameters for the run
    parser.add_argument("--until", action="store", type=int,
                        default="100",
                        help="How long (min) to run the simulation")
    parser.add_argument("--config_json", action="store", type=str,
                        help="Configuration json to use for the run",
                        default=None)
    # Log level
    parser.add_argument("--log_level", action="store", type=str,
                        default="WARN",
                        help="Log level")

    args = parser.parse_args()

    # Config logging
    numeric_level = getattr(logging, args.log_level.upper(), None)
    logging.basicConfig(format='%(asctime)s %(message)s', level=numeric_level)

    # If there is no config dict specified, just bail hard.
    if not args.config_json:
        logging.error("Must specify a configuration file!")
        print("Must specify a configuration file!")
        sys.exit(-1)


    logging.info("Starting...")

    # Load up the config file
    logging.info("Loading model constructors...")
    config_dict = config_reader.read_config_json(args.config_json)

    env, system, start = load_gtfs(config_dict)

    # Now actually run it
    run_system(env, system, until=(args.until+start))
