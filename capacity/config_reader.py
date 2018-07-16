""" Load the configs and queue up the constructors """

import json
import logging
import os.path

import capacity.models.model_reg as model_reg

# This specifies all the files and their defaults
DEFAULT_FILES = {
    "traveler_stat_file": "traveler.log",
    "network_stat": "network_stat.log"
}

def build_path_dict(run_prefix, config_json):
    """Figure out all the important file paths"""
    # First, did the config specify a file section at all?
    if "files" not in config_json:
        # If not just pretend its blank so we take all defaults
        file_dict = {}
    else:
        file_dict = config_json["files"]

    path_dict = {}

    # Now let's spin over the files
    for out_file in DEFAULT_FILES:
        # They specified an override
        if out_file in file_dict:
            base_file = file_dict[out_file]
        # No override, take default
        else:
            base_file = DEFAULT_FILES[out_file]

        # Build the full path
        full_file = os.path.join(run_prefix, base_file)

        # Staple it into the dict
        path_dict[out_file] = full_file

    return path_dict

def read_config_json(config_file):
    """ Load up the config json """

    # If we got passed nothing, just return blank
    if config_file is None:
        logging.warn("No config specified, using full default!")
        # TODO: think this case might need to do more work
        return {}

    logging.info("Loading configuration from %s", config_file)

    # Just read the json and spit, nothin' fancy
    try:
        with open(config_file, 'r') as config_file_obj:
            config_json = json.load(config_file_obj)
    except FileNotFoundError as error:
        logging.critical("Couldn't find configuration file!")
        raise error

    # Let's loop through each and grab the appropriate function
    const_dict = {}

    # Grab the main outdir
    const_dict["run_dir"] = config_json["run_dir"]
    # Build dict of file names using defaults or overrides
    const_dict["files"] = build_path_dict(const_dict["run_dir"],
                                          config_json)
    # If there is a start time, grab that
    if "start_time" in config_json:
        const_dict["start_time"] = config_json["start_time"]

    for model in config_json["models"]:
        # Only one name per model
        name = list(config_json["models"][model].keys())[0]
        params = config_json["models"][model][name]
        class_init = model_reg.load_model(model, name, params)

        const_dict[model] = class_init

    return const_dict
