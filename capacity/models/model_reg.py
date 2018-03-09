""" Manages the loading of modules for each model """

import os
import os.path
import importlib.util
import sys

def load_model(model_type, name, params):
    """Load the specified model"""

    #First, let's build the path
    curr_path = os.path.dirname(sys.modules[__name__].__file__)
    path = os.path.join(curr_path, model_type, name+".py")

    # Create spec from the file
    spec = importlib.util.spec_from_file_location("capacity.models.%s"%model_type,
                                                  path)
    # Create and load the module
    model_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model_mod)

    # Return the argument free constructor
    return model_mod.instantiate(params)
