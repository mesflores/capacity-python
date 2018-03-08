import json
import logging

import capacity.models.model_reg as model_reg

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
    for model in config_json:
        # Only one name per model
        name = list(config_json[model].keys())[0]
        params = config_json[model][name]
        class_init = model_reg.load_model(model, name, params)

        const_dict[model] = class_init

    return const_dict

