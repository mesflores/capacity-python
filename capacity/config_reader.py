import json
import logging

def read_config_json(config_file):
    """ Load up the config json """

    # If we got passed nothing, just return blank
    if config_file is None:
        logging.warn("No config specified, using full default!")
        return {}

    logging.info("Loading configuration from %s", config_file)

    # Just read the json and spit, nothin' fancy
    try:
        with open(config_file, 'r') as config_file_obj:
            config_json = json.read(config_file_obj)
    except FileNotFoundError as error:
        logging.critical("Couldn't find configuration file!")
        raise error

    return config_json

